export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Método não permitido' });
    }

    const { prompt } = req.body;
    const API_KEY = "AQ.Ab8RN6K9nVvNcnnjMh5fDNgZSkllNtk88oYbvVMTq0vDaIO2Kg";

    try {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${API_KEY}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{ parts: [{ text: prompt }] }]
            })
        });

        const data = await response.json();

        if (data && data.candidates && data.candidates[0].content.parts[0].text) {
            return res.status(200).json({ text: data.candidates[0].content.parts[0].text });
        } else {
            return res.status(500).json({ error: 'Erro ao processar resposta da IA' });
        }
    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
}
