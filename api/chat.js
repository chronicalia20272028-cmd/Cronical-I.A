module.exports = async (req, res) => {
    // Configura os cabeçalhos de CORS
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
    res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const apiKey = process.env.GEMINI_API_KEY;
        if (!apiKey) {
            return res.status(500).json({ error: 'ERRO: A variável GEMINI_API_KEY não está configurada na Vercel!' });
        }

        const { contents } = req.body || {};
        if (!contents) {
            return res.status(400).json({ error: 'ERRO: O corpo do pedido (contents) chegou vazio.' });
        }

        const modelName = "gemini-1.5-flash";
        const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent`;

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({ contents })
        });

        const responseText = await response.text();

        if (!response.ok) {
            return res.status(500).json({ error: `Google API Error (${response.status}): ${responseText}` });
        }

        const data = JSON.parse(responseText);
        return res.status(200).json(data);

    } catch (error) {
        return res.status(500).json({ error: `Erro interno no servidor: ${error.message}` });
    }
};
