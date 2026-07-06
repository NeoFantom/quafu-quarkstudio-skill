# Deployments

## 2026-07-06 14:09 CST — BAQIS Quafu Skill group-meeting page

- Public URL: https://what.usay.dev/quafu-skill/
- Server: tcserver / what.usay.dev
- Backing path: `/srv/what.usay.dev/sites/quafu-skill/`
- Serving mechanism: nginx static alias at `/quafu-skill/`
- Local source: `site/quafu-skill/index.html`
- Source commit at deploy time: `c9b3a94`
- Deploy commands:
  - `mkdir -p /srv/what.usay.dev/sites/quafu-skill`
  - `rsync -av --delete site/quafu-skill/ tc:/srv/what.usay.dev/sites/quafu-skill/`
  - Updated `/etc/nginx/sites-enabled/what.usay.dev` with a `/quafu-skill/` alias block.
  - `sudo nginx -t && sudo systemctl reload nginx`
- Server map: added `https://what.usay.dev/quafu-skill/` row to `~/hosted-sites-map.md`.
- Verification:
  - `https://what.usay.dev/quafu-skill/` returned `200 text/html`.
  - `https://what.usay.dev/quafu-skill/__missing__` returned `404`.
  - Public HTML contained the key presentation strings for `BAQIS Quafu Skill`, skill-vs-cloud-agent distinction, `quafu-skill`, and `baqis-quafu`.
