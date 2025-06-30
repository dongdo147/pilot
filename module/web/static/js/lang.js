export function setupLanguageSelector({
    langSelectorId = 'langSelect',
    elements = [],
    defaultLang = 'en',
    apiUrlBase = '/api/translations',
    section = null
} = {}) {
    const langSelect = document.getElementById(langSelectorId);

    function updateTranslations(lang) {
        let apiUrl = `${apiUrlBase}?lang=${lang}`;
        if (section) {
            apiUrl += `&section=${section}`;
        }

        fetch(apiUrl)
            .then(res => res.json())
            .then(data => {
                elements.forEach(key => {
                    const els = document.getElementsByClassName(key);
                    Array.from(els).forEach(el => {
                        if (data[key]) {
                            el.textContent = data[key];
                        }
                    });
                });
            })
            .catch(err => console.error('Translation error:', err));
    }

    if (langSelect) {
        langSelect.addEventListener('change', (e) => {
            const selectedLang = e.target.value;
            localStorage.setItem('lang', selectedLang);
            location.reload();  // 🔁 Reload lại trang để áp dụng
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        const savedLang = localStorage.getItem('lang') || defaultLang;
        if (langSelect) langSelect.value = savedLang;
        updateTranslations(savedLang);
    });
}
