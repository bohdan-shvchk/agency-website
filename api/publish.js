export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { slug, content, secret } = req.body;

  if (secret !== process.env.PUBLISH_SECRET) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  if (!slug || !content) {
    return res.status(400).json({ error: 'Missing slug or content' });
  }

  const token = process.env.GITHUB_TOKEN;
  const repo = 'bohdan-shvchk/agency-website';
  const path = `src/content/blog/${slug}.md`;
  const encoded = Buffer.from(content).toString('base64');

  const checkRes = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`, {
    headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' },
  });

  const body = { message: `feat: add ${slug} blog post`, content: encoded };

  if (checkRes.ok) {
    const existing = await checkRes.json();
    body.sha = existing.sha;
  }

  const pushRes = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`, {
    method: 'PUT',
    headers: {
      Authorization: `token ${token}`,
      Accept: 'application/vnd.github.v3+json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  const result = await pushRes.json();

  if (result.content?.sha) {
    return res.status(200).json({ ok: true, slug, url: `/blog/${slug}` });
  }

  return res.status(500).json({ error: result.message || 'GitHub API error' });
}
