# Publishing atlaspi-mcp to PyPI

Two paths:

## Option A: Trusted Publisher (recommended, one-time setup)

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in:
   - PyPI project name: `atlaspi-mcp`
   - Owner: `Soil911`
   - Repository name: `AtlasPI`
   - Workflow name: `publish-mcp.yml`
   - Environment name: `pypi`
4. Create a PyPI account if you don't have one.

Once configured, publish by pushing a tag:
```bash
git tag mcp-v0.7.0
git push origin mcp-v0.7.0
```

GitHub Actions picks it up automatically — no API token needed.

## Option B: Manual upload (faster for first release)

1. Create PyPI account at https://pypi.org/account/register/
2. Generate API token at https://pypi.org/manage/account/token/
3. Build and upload locally:
   ```bash
   cd mcp-server
   python -m build
   python -m twine upload dist/*
   # When prompted: username = __token__, password = pypi-<your-token>
   ```

## Verifying the publish

After either path:
```bash
pip install atlaspi-mcp
atlaspi-mcp --help
```

Or in Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):
```json
{
  "mcpServers": {
    "atlaspi": {
      "command": "atlaspi-mcp"
    }
  }
}
```

## Package metadata

- **Name**: `atlaspi-mcp`
- **Version**: 0.7.0 (34 MCP tools)
- **License**: Apache-2.0
- **Python**: >=3.10
- **Homepage**: https://atlaspi.cra-srl.com
- **Source**: https://github.com/Soil911/AtlasPI

## Version bumping

When releasing a new version:
1. Update `version = "X.Y.Z"` in `pyproject.toml`
2. Update `__version__ = "X.Y.Z"` in `src/atlaspi_mcp/__init__.py`
3. Commit
4. Tag: `git tag mcp-vX.Y.Z && git push origin mcp-vX.Y.Z`

The `publish-mcp.yml` GitHub Actions workflow triggers automatically on `mcp-v*` tags.
