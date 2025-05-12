document.addEventListener('DOMContentLoaded', function() {
    const addSubjectBtn = document.getElementById('addSubjectBtn');
    const cancelFormBtn = document.getElementById('cancelFormBtn');
    const subjectFormContainer = document.getElementById('subjectFormContainer');
    const subjectForm = document.getElementById('subjectForm');
    const subjectIdInput = document.getElementById('subjectId');

    const generateAbbrBtn = document.getElementById('generateAbbrBtn');
    if (generateAbbrBtn) {
        generateAbbrBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const fullNameInput = document.getElementById('fullSubjectName');
            const abbreviationOutput = document.getElementById('generatedAbbreviation');
            
            if (!fullNameInput || !abbreviationOutput) {
                console.error('Не найдены необходимые элементы на странице');
                return;
            }
            
            const fullName = fullNameInput.value.trim();
            if (!fullName) {
                showNotification('Введите название предмета', 'warning');
                return;
            }
            
            const abbreviation = generateAbbreviation(fullName);
            abbreviationOutput.value = abbreviation;

            const abbrField = document.getElementById('abbr');
            if (abbrField && document.getElementById('subjectFormContainer').style.display === 'block') {
                abbrField.value = abbreviation;
                showNotification('Аббревиатура сгенерирована и добавлена в форму', 'success');
            }
        });
    }

    function generateAbbreviation(fullName) {
        if (!fullName) return '';
        
        const stopWords = ['и', 'на', 'в', 'с', 'по', 'для', 'о', 'у', 'за', 'над', 'под'];
        const words = fullName.split(' ');
        let abbreviation = '';
        
        for (let word of words) {
            word = word.trim();
            if (!word) continue;

            if (word.toLowerCase() === 'и') {
                abbreviation += 'и';
                continue;
            }

            if (stopWords.includes(word.toLowerCase())) {
                continue;
            }

            abbreviation += word[0].toUpperCase();
        }
        
        return abbreviation;
    }

    addSubjectBtn.addEventListener('click', function() {
        subjectForm.reset();
        subjectIdInput.value = '';
        subjectFormContainer.style.display = 'block';
        document.getElementById('title').focus();
    });

    cancelFormBtn.addEventListener('click', function() {
        subjectFormContainer.style.display = 'none';
    });

    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            const title = this.getAttribute('data-title');
            const abbr = this.getAttribute('data-abbr');
            const files = this.getAttribute('data-files');
            const params = this.getAttribute('data-params');
            
            document.getElementById('title').value = title;
            document.getElementById('abbr').value = abbr;
            document.getElementById('files_count').value = files;
            document.getElementById('review_params').value = params || '';
            subjectIdInput.value = id;
            
            subjectFormContainer.style.display = 'block';
            window.scrollTo({
                top: subjectFormContainer.offsetTop - 20,
                behavior: 'smooth'
            });
        });
    });
    
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            if (confirm('Вы уверены, что хотите удалить этот предмет?')) {
                fetch(`/api/delete-subject/${id}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCSRFToken(),
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                })
                .then(handleResponse)
                .then(data => {
                    if (data.success) {
                        showNotification('Предмет успешно удален', 'success');
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        showNotification('Ошибка при удалении: ' + (data.error || 'Неизвестная ошибка'), 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('Произошла ошибка при удалении', 'error');
                });
            }
        });
    });
    
    subjectForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new URLSearchParams();
        for (const pair of new FormData(subjectForm)) {
            formData.append(pair[0], pair[1]);
        }
        
        const url = subjectIdInput.value 
            ? `/api/update-subject/${subjectIdInput.value}/` 
            : '/api/add-subject/';
        
        const method = subjectIdInput.value ? 'UPDATE' : 'CREATE';
        
        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        })
        .then(handleResponse)
        .then(data => {
            if (data.success) {
                showNotification(
                    subjectIdInput.value 
                        ? 'Предмет успешно обновлен' 
                        : 'Предмет успешно добавлен', 
                    'success'
                );
                setTimeout(() => location.reload(), 1000);
            } else {
                showNotification('Ошибка: ' + (data.error || 'Неизвестная ошибка'), 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Произошла ошибка при сохранении', 'error');
        });
    });

    function getCSRFToken() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfInput ? csrfInput.value : '';
    }

    function handleResponse(response) {
        if (!response.ok) {
            return response.text().then(text => {
                try {
                    return JSON.parse(text);
                } catch {
                    throw new Error(text || 'Server error');
                }
            });
        }
        return response.json();
    }

    function showNotification(message, type = 'info') {
        alert(`${type.toUpperCase()}: ${message}`);
    }

    const copyAbbrBtn = document.getElementById('copyAbbrBtn');
    if (copyAbbrBtn) {
        copyAbbrBtn.addEventListener('click', function() {
            const abbrField = document.getElementById('generatedAbbreviation');
            if (!abbrField || !abbrField.value) {
                showNotification('Нет аббревиатуры для копирования', 'warning');
                return;
            }
            
            navigator.clipboard.writeText(abbrField.value)
                .then(() => showNotification('Аббревиатура скопирована', 'success'))
                .catch(err => {
                    console.error('Ошибка копирования: ', err);
                    showNotification('Не удалось скопировать аббревиатуру', 'error');
                });
        });
    }
});