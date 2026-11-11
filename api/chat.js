try {
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contents: [...] }) // o teu array de mensagens atual
    });

    const text = await response.text(); // Lê primeiro como texto bruto para evitar o erro de JSON
    const data = text ? JSON.parse(text) : {};

    if (!response.ok) {
        throw new Error(data.error || 'Erro desconhecido no servidor');
    }

    // Processa a resposta normal do Gemini aqui...
    const reply = data.candidates?.[0]?.content?.parts?.[0]?.text;
    console.log(reply);

} catch (err) {
    console.error("Erro capturado:", err.message);
    alert("Erro ao processar: " + err.message);
}
