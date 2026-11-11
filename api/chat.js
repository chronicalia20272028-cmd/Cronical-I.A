export default async function handler(req, res) {
    // Configura os cabeçalhos de CORS para garantir compatibilidade
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
    res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { contents } = req.body;
        if (!contents) {
            return res.status(400).json({ error: 'Payload vazio ou inválido.' });
        }

        const modelName = "gemini-1.5-flash";
        const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent`;
        const apiKey = process.env.GEMINI_API_KEY;

        if (!apiKey) {
            return res.status(500).json({ error: 'GEMINI_API_KEY não configurada nas variáveis da Vercel.' });
        }

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({ contents })
        });

        const textResponse = await response.text();
        
        let data;
        try {
            data = JSON.parse(textResponse);
        } catch (e) {
            return res.status(500).json({ error: `Resposta inválida da API Google: ${textResponse}` });
        }

        return res.status(200).json(data);
    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
}
