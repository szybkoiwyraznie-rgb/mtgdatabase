const ALLOWED_FIELDS = ["feeling", "story_fit", "sample_quality"];

function cors(origin, env) {
  // A project Pages site has the owner's github.io origin. Do not grant the
  // feedback endpoint to every unrelated GitHub Pages site.
  const owner = String(env.GITHUB_REPOSITORY || "").split("/", 1)[0];
  const expectedOrigin = owner ? `https://${owner}.github.io` : "";
  const headers = {
    "Access-Control-Allow-Headers": "content-type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Content-Type": "application/json"
  };
  // Do not return the literal "null" value: that would grant a CORS response
  // to sandboxed or local documents which present Origin: null.
  if (origin === expectedOrigin) headers["Access-Control-Allow-Origin"] = expectedOrigin;
  return headers;
}

function response(body, status, origin, env) {
  return new Response(JSON.stringify(body), { status, headers: cors(origin, env) });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin");
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(origin, env) });
    if (request.method !== "POST") return response({ error: "POST required" }, 405, origin, env);

    let payload;
    try { payload = await request.json(); } catch { return response({ error: "Invalid JSON" }, 400, origin, env); }
    const { story_id, version, comment = "", scores = {} } = payload;
    if (!/^[A-Za-z0-9_-]{1,64}$/.test(String(story_id || ""))) return response({ error: "Invalid story_id" }, 400, origin, env);
    if (!/^v[0-9]+$/.test(String(version || ""))) return response({ error: "Invalid version" }, 400, origin, env);
    if (String(comment).length > 2000) return response({ error: "Comment too long" }, 400, origin, env);
    if (ALLOWED_FIELDS.some(field => !Number.isInteger(scores[field]) || scores[field] < 1 || scores[field] > 5)) {
      return response({ error: "Scores must be integers from 1 to 5" }, 400, origin, env);
    }

    const total = ALLOWED_FIELDS.reduce((sum, field) => sum + scores[field], 0);
    const title = `Feedback ${story_id} ${version} — ${total}/15`;
    const body = [
      `<!-- jingle-feedback: ${story_id}:${version} -->`,
      `**Story:** ${story_id}`,
      `**Version:** ${version}`,
      `**Feeling:** ${scores.feeling}/5`,
      `**Story fit:** ${scores.story_fit}/5`,
      `**Sample quality:** ${scores.sample_quality}/5`,
      `**Total:** ${total}/15`,
      "", "**Comment:**", String(comment).trim() || "_No comment._"
    ].join("\n");

    const githubResponse = await fetch(`https://api.github.com/repos/${env.GITHUB_REPOSITORY}/issues`, {
      method: "POST",
      headers: {
        "Accept": "application/vnd.github+json",
        "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
        "User-Agent": "jingle-feedback-worker",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ title, body, labels: ["feedback", "needs-review", `story:${story_id}`] })
    });
    if (!githubResponse.ok) return response({ error: "GitHub issue creation failed" }, 502, origin, env);
    const issue = await githubResponse.json();
    return response({ ok: true, issue_url: issue.html_url }, 201, origin, env);
  }
};
