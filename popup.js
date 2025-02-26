document.addEventListener('DOMContentLoaded', () => {
    const detectButton = document.getElementById('detect-language');
    const languageInput = document.getElementById('language-input'); // Add input field

    detectButton.addEventListener('click', () => {
        const targetLanguage = languageInput.value.trim().toLowerCase(); // Get input
        if (!targetLanguage) {
            document.getElementById('result').textContent = "Please enter a language code.";
            return;
        }

        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const activeTab = tabs[0];

            fetch('https://afternoon-coast-99166-a615ff05647b.herokuapp.com/detect-language', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: activeTab.url, target_language: targetLanguage }) // Send input
            })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('result').textContent = `Error: ${data.error}`;
                    } else {
                        const languageCounts = data.language_counts;
                        const targetWords = data.language_words;
                        let resultText = '';

                        if (targetLanguage in languageCounts && languageCounts[targetLanguage] > 0) {
                            resultText += `Localisation exists for ${targetLanguage} (Count: ${languageCounts[targetLanguage]}).\n`;
                            resultText += `\n Words are : \n${targetWords.join(',')}\n`;
                            
                        } else {
                            resultText = `No ${targetLanguage} words detected.\n`;
                        }

                        document.getElementById('result').textContent = resultText;
                    }
                })
                .catch(err => {
                    document.getElementById('result').textContent = `Failed to fetch data:-> ${err}`;
                });
        });
    });
});