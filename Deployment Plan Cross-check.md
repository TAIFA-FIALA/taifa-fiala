# Deployment Plan Cross-check

I just wanted to make sure that we have documented some of the key things that need to happen for deployment. This is going to go to three different places.

1.  The Python backend is going to my local server on Tailscale. That is already written into the deployment script in the root. It will need to be refactored, but that part is already clear.
2.  The Next.js frontend is going to Vercel through a CI/CD pathway on my personal GitHub that is linked to the repo on the org site. There should ber a section of the deploy script already that copies over the Next.js frontend to a separate public repo.
3.  The Streamlit app is staying local. I don't know how I'm going to launch it from the headless server, unless you can give me some suggestions.

That's the end of this note for deployment. 