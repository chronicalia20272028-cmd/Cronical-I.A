const { GoogleGenAI } = require('@google/genai');

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

        let bodyData = req.body;
        if (!bodyData || (typeof bodyData === 'object' && Object.keys(bodyData).length === 0)) {
            let raw = '';
            for await (const chunk of req) {
                raw += chunk;
            }
            if (raw) {
                try { bodyData = JSON.parse(raw); } catch (e) { bodyData = {}; }
            }
        }

        const contents = bodyData?.contents;
        if (!contents) {
            return res.status(400).json({ error: 'Conteúdo da mensagem vazio.' });
        }

        // Inicializa o SDK oficial do Google GenAI com a chave AQ...
        const ai = new GoogleGenAI({ apiKey: apiKey });

        // Extrai a última mensagem do utilizador para enviar ao modelo
        const lastMessage = contents[contents.length - 1]?.parts?.[0]?.text || "Olá";

        const response = await ai.models.generateContent({
            model: 'gemini-1.5-flash',
            contents: lastMessage,
        });

        // Formata a resposta exatamente como o teu index.html espera
        const formattedResponse = {
            candidates: [
                {
                    content: {
                        parts: [
                            { text: response.text }
                        ]
                    }
                }
            ]
        };

        return res.status(200).json(formattedResponse);

    } catch (err) {
        return res.status(500).json({ error: 'Erro no servidor: ' + err.message });
    }
};
