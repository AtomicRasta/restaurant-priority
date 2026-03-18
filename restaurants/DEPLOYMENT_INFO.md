# Restaurant App - Live Deployment

## Live URLs

**Main App:** https://restaurant-deploy-nine.vercel.app/
**Priority Editor:** https://restaurant-deploy-nine.vercel.app/priority-editor
**GitHub Repo:** https://github.com/AtomicRasta/restaurant-priority

## Deployment Details

- **Deployed:** March 17, 2026
- **Platform:** Vercel
- **Source:** GitHub (auto-deploys on push)
- **Project Name:** restaurant-deploy

## Accessing from Phone

You can now access the priority editor from your phone anywhere in the world:
- Just open: https://restaurant-deploy-nine.vercel.app/priority-editor
- Bookmark it for quick access
- Share the link with friends

## Updating the Live Site

To update the deployed version:

1. **Make changes** to files in `/Users/rastamacmini/Desktop/restaurant-deploy/`
2. **Commit and push:**
   ```bash
   cd ~/Desktop/restaurant-deploy
   git add .
   git commit -m "Your update message"
   git push
   ```
3. **Vercel auto-deploys** - live in ~10 seconds

## Files Structure

- `index.html` - Weekly availability checker
- `priority-editor.html` - Drag-drop restaurant prioritization
- `restaurant-priority.json` - Restaurant data
- `vercel.json` - Deployment configuration

## Sharing with Friends

Just send them: https://restaurant-deploy-nine.vercel.app/priority-editor

They can view and interact with your restaurant list. If you want them to be able to save changes, you'd need to add authentication (future enhancement).
