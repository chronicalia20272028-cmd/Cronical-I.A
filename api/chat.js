module.exports = async (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const apiKey = process.env.GEMINI_API_KEY;
        if (!apiKey) {
            return res.status(500).json({ error: 'GEMINI_API_KEY em falta nas variáveis da Vercel.' });
        }

        // Leitura robusta do body (funciona quer venha parseado ou como stream)
        let bodyData = req.body;
        if (!bodyData || (typeof bodyData === 'object' && Object.keys(bodyData).length === 0)) {
            let raw = '';
            for await (const chunk of req) {
                raw += chunk;
            }
            if (raw) {
                try {
                    bodyData = JSON.parse(raw);
                } catch (e) {
                    bodyData = {};
                }
            }
        }

        const contents = bodyData?.contents;
        if (!contents) {
            return res.status(400).json({ error: 'Conteúdo da mensagem vazio (contents em falta).' });
        }

        const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent`;

        const apiResponse = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({ contents })
        });

        const rawText = await apiResponse.text();
        
        let data;
        try {
            data = JSON.parse(rawText);
        } catch (e) {
            return res.status(500).json({ error: `Resposta inválida do Google: ${rawText}` });
        }

        if (!apiResponse.ok) {
            return res.status(500).json({ error: data?.error?.message || `Erro Google API (${apiResponse.status}): ${rawText}` });
        }

        return res.status(200).json(data);

    } catch (err) {
        return res.status(500).json({ error: 'Erro interno no servidor: ' + err.message });
    }
};
