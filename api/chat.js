import { GoogleGenAI } from '@google/genai';

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Método não permitido' });
    }

    const { prompt } = req.body;
    const API_KEY = "AQ.Ab8RN6K9nVvNcnnjMh5fDNgZSkllNtk88oYbvVMTq0vDaIO2Kg";

    try {
        const ai = new GoogleGenAI({ apiKey: API_KEY });

        const response = await ai.models.generateContent({
            model: 'gemini-1.5-flash',
            contents: prompt,
        });

        if (response && response.text) {
            return res.status(200).json({ text: response.text });
        } else {
            return res.status(500).json({ error: 'Resposta vazia da IA' });
        }
    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
}
