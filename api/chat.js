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
        // Garantir leitura correta do corpo do pedido em ambiente Vercel
        const body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body;
        const prompt = body?.prompt;

        if (!prompt) {
            return res.status(400).json({ error: 'Prompt não fornecido' });
        }

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
            return res.status(200).json({ text: data.candidates[0].content.parts[0].text });
        } else if (data.error) {
            return res.status(500).json({ error: data.error.message });
        } else {
            return res.status(500).json({ error: 'Estrutura de resposta inválida da Google' });
        }
    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
}
