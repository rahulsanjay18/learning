# Keeping some of the learning site private on a free tier (2026-10-07)

## TL;DR
- **GitHub Pages can't do private on the free plan.** Free plans publish Pages only from public repos [1][2], and restricting who can
  *view* a Pages site needs GitHub Enterprise Cloud [3]. A private repo on a paid plan still serves a public site [3].
- **Recommended: split by sensitivity, not by host.**
  1. **Public (GitHub Pages, as now):** lesson pages, widgets, programs. Nothing personal.
  2. **Private data at runtime → your own server**, which you already run (`books.tail59e10.ts.net`, the progress server). Public
     pages fetch private data with your device token, the same way review and progress already work. The page is public, the data isn't.
  3. **Private files → a second, private GitHub repo** (e.g. `learning-private`): the inbox, brag doc, pay notes. It's never published;
     you read it in GitHub's app or web UI, and Claude sessions can attach it like the 3D chess repos.
- **If you want the whole site private:** Cloudflare Pages (deploys from private repos [5]) behind Cloudflare Access (free Zero Trust
  plan, up to 50 users [4]; check current terms) with an email one-time-PIN login. You already use Cloudflare for the game.
  Watch out: protect both the custom domain and the `*.pages.dev` address, and preview URLs [6].
- **Not recommended for anything sensitive: password-encrypting pages (StatiCrypt).** It's AES in the browser, but the ciphertext is
  public, so it's only as strong as the passphrase, and the author says not to use it for very sensitive data [7]. It also hides
  nothing about file names or git history.
- **Already public stays public:** anything pushed to this repo is in its git history, even if deleted later.

## Sources
1. GitHub Docs, *Creating a GitHub Pages site* (availability by plan). https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site
2. GitHub Community discussion #22817, *Publish with GitHub Pages keeping repo as private on free plan*. https://github.com/orgs/community/discussions/22817
3. GitHub Docs (Enterprise Cloud), *Changing the visibility of your GitHub Pages site*. https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/changing-the-visibility-of-your-github-pages-site
4. Cloudflare blog, *Teams plans* (free plan up to 50 users; 2020, background). https://blog.cloudflare.com/teams-plans ; current terms per CostBench, *Cloudflare Zero Trust Free Plan 2026*. https://costbench.com/software/business-vpn/cloudflare-zero-trust/free-plan/
5. Cloudflare Docs, *Pages Git integration* (private repos supported). https://developers.cloudflare.com/pages/platform/git-integration/
6. Revdoku, *Cloudflare Pages password protection with Access* (hostnames and previews). https://revdoku.com/blog/how-to-password-protect-a-cloudflare-pages-site/
7. StatiCrypt via DEV Community (AES-256 in the browser; caveats). https://dev.to/manishfoodtechs/staticrypt-password-protect-a-static-html-page-1e1h
