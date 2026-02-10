# Seed Query Demo

Lightweight static demo for:

1. Paste seed queries
2. Click **Run**
3. Preview generated JSONL
4. Download `.jsonl`

## Files

- `index.html` UI layout
- `styles.css` minimal styling
- `app.js` conversion + download logic

## Run Locally

From repository root:

```bash
cd demo
python3 -m http.server 8080
```

Open [http://localhost:8080](http://localhost:8080).

## Deploy (Static Hosting)

### Option 1: GitHub Pages

1. Push repository to GitHub.
2. Go to **Settings → Pages**.
3. Set source to your branch and folder:
   - branch: `main` (or your default branch)
   - folder: `/demo` (or `/` if you publish only this folder)
4. Save and wait for deployment.

### Option 2: Netlify

1. Create a new site from your repo.
2. Set **Publish directory** to `demo`.
3. Build command is not required (leave empty).
4. Deploy.

### Option 3: Vercel

1. Import the repository in Vercel.
2. Set **Output Directory** to `demo`.
3. No build command required.
4. Deploy.

## Notes

- Input format: one seed query per line.
- Blank lines are ignored.
- Duplicate removal is enabled by default and can be toggled off.
