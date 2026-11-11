export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Método não permitido' });
    }

    try {
        let prompt = "";
        if (typeof req.body === 'string') {
            const parsed = JSON.parse(req.body);
            prompt = parsed.prompt;
        } else if (req.body && req.body.prompt) {
            prompt = req.body.prompt;
        }

        if (!prompt) {
            return res.status(400).json({ error: 'Prompt vazio' });
        }

        // A tua chave oficial configurada em segurança no servidor da Vercel
        const API_KEY = "AQ.Ab8RN6K9nVvNcnnjMh5fDNgZSkllNtk88oYbvVMTq0vDaIO2Kg";

        const apiResponse = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${API_KEY}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{ parts: [{ text: prompt }] }]
            })
        });

        const data = await apiResponse.json();

        if (data && data.candidates && data.candidates[0].content.parts[0].text) {
            const aiText = data.candidates[0].content.parts[0].text;
            return res.status(200).json({ text: aiText });
        } else if (data.error) {
            return res.status(500).json({ error: data.error.message });
        } else {
            return res.status(500).json({ error: 'Resposta inválida da API da Google' });
        }
    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
}
