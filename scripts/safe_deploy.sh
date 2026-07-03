#!/usr/bin/env bash
# v6.99.29 — safe wrapper for cra-deploy with auto-revert on healthcheck fail.
# Usage: bash scripts/safe_deploy.sh [iter_number]
# Returns 0 if deployed OK, 1 if reverted (so the caller can skip iteration).

set -u
ITER="${1:-?}"
LOG_FILE="data/enrichment/LOOP_STATE.md"
START_HASH=$(git rev-parse HEAD)
START_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "[safe_deploy] iter=$ITER start_hash=$START_HASH"

# 1. Push (if anything to push)
if ! git push origin main 2>&1 | tee /tmp/safe_deploy_push.log; then
    echo "[safe_deploy] git push FAILED — aborting deploy, no changes pushed"
    exit 1
fi

# 2. Deploy via cra-deploy
if ! "$HOME/bin/cra-deploy.sh" atlaspi 2>&1 | tee /tmp/safe_deploy_cra.log; then
    DEPLOY_RC=$?
    echo "[safe_deploy] cra-deploy returned $DEPLOY_RC"
    # cra-deploy itself already does a healthcheck, so failure here means the
    # service didn't come up. We must roll back the commit.
    echo "[safe_deploy] cra-deploy FAILED at $(date -u +%TZ) — auto-reverting"
    REVERT_MSG="auto-revert: cra-deploy failed in loop iter $ITER (was $START_HASH)"
    git revert --no-edit "$START_HASH" || {
        echo "[safe_deploy] git revert FAILED — manual intervention required"
        exit 2
    }
    git push origin main
    "$HOME/bin/cra-deploy.sh" atlaspi || echo "[safe_deploy] revert deploy also failed — SERIOUS"
    {
        echo ""
        echo "## ⚠️ AUTO-REVERT $START_TIME"
        echo "- Iter: $ITER"
        echo "- Reverted commit: $START_HASH"
        echo "- Reason: cra-deploy healthcheck failed"
        echo "- See: /tmp/safe_deploy_cra.log on this machine"
    } >> "$LOG_FILE"
    exit 1
fi

# 3. Extra post-deploy verification via public health endpoint
for i in 1 2 3; do
    if curl -fsS -m 10 https://atlaspi.it/health > /tmp/safe_deploy_health.json 2>&1; then
        echo "[safe_deploy] healthcheck pass on attempt $i"
        break
    fi
    if [ "$i" = "3" ]; then
        echo "[safe_deploy] healthcheck FAILED 3x — auto-reverting"
        git revert --no-edit "$START_HASH" || exit 2
        git push origin main
        "$HOME/bin/cra-deploy.sh" atlaspi
        {
            echo ""
            echo "## ⚠️ AUTO-REVERT $START_TIME"
            echo "- Iter: $ITER"
            echo "- Reverted commit: $START_HASH"
            echo "- Reason: public /health endpoint failed 3x post-deploy"
        } >> "$LOG_FILE"
        exit 1
    fi
    sleep 5
done

echo "[safe_deploy] iter=$ITER deployed OK"
exit 0
