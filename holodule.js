window.addEventListener('DOMContentLoaded', main);

function main() {
    setLastTheme();
    setNameList();
    registerEventListeners();
}

function setLastTheme() {
    const theme = localStorage.getItem('theme');
    if (theme !== null) {
        document.body.setAttribute('class', theme);
        const themeSelectBox = document.querySelector('#theme');
        themeSelectBox.value = theme;
    }
}

// 名前選択ボックスに名前を追加
function setNameList() {
    let names = Array.from(document.querySelectorAll('#holodule_tbody td.name')).map(td => td.textContent.trim());
    const nameSet = new Set();
    names.forEach(name => {
        nameSet.add(name);
    });
    names = [...nameSet];
    names.sort();

    const nameSelectBox = document.querySelector('#name_to_filter2');
    names.forEach(name => {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name;
        nameSelectBox.appendChild(option);
    });
}

function registerEventListeners() {
    const nameSelectBox = document.querySelector('#name_to_filter2');
    const nameToFilter = document.querySelector('#name_to_filter');
    const dateToFilter = document.querySelector('#date_to_filter');
    const clearDateButton = document.querySelector('#clear_date_button');
    const clearAllButton = document.querySelector('#clear_all_button');
    const themeSelectBox = document.querySelector('#theme');

    nameSelectBox.addEventListener('change', (e) => {
        nameToFilter.value = '';
        const name = nameSelectBox.value;
        const date = new Date(dateToFilter.value);
        filterStreams({ 'name': name, 'date': date });
    }, false);

    nameToFilter.addEventListener('input', (e) => {
        nameSelectBox.value = '';
        const name = nameToFilter.value;
        const date = new Date(dateToFilter.value);
        filterStreams({ 'name': name, 'date': date });
    }, false);

    dateToFilter.addEventListener('change', (e) => {
        const name = nameSelectBox.value || nameToFilter.value;
        const date = new Date(dateToFilter.value);
        filterStreams({ 'name': name, 'date': date });
    }, false);

    clearDateButton.addEventListener('click', (e) => {
        const name = nameSelectBox.value || nameToFilter.value;
        dateToFilter.value = '';
        filterStreams({ 'name': name });
    }, false);

    clearAllButton.addEventListener('click', (e) => {
        nameSelectBox.value = '';
        nameToFilter.value = '';
        dateToFilter.value = '';
        filterStreams({});
    }, false);

    themeSelectBox.addEventListener('change', (e) => {
        const theme = themeSelectBox.value;
        document.body.setAttribute('class', theme);
        localStorage.setItem('theme', theme);
    }, false);
}

function filterStreams(options) {
    const holoduleTableBody = document.querySelector('#holodule_tbody');

    console.log('filterStreams', options);

    const normalizeName = (name) => name.toLowerCase();

    const trs = Array.from(holoduleTableBody.querySelectorAll('tr'));
    trs.forEach(tr => {
        tr.classList.remove('hidden');
    });

    if ('name' in options && options.name !== '') {
        options.name = normalizeName(options.name);
        trs.forEach(tr => {
            const name = normalizeName(tr.querySelector('td.name').textContent.trim());
            if (!name.includes(options.name)) {
                tr.classList.add('hidden');
            }
        });
    }
    if ('date' in options && !isNaN(options.date.getTime())) {
        trs.forEach(tr => {
            const date = new Date(tr.querySelector('td.starts_at').textContent.trim());
            if (options.date.getYear() !== date.getYear() ||
                options.date.getMonth() !== date.getMonth() ||
                options.date.getDate() !== date.getDate()) {
                tr.classList.add('hidden');
            }
        });
    }
}
