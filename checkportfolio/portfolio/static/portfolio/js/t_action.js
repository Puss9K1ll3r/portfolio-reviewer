document.addEventListener('DOMContentLoaded', function() {
    const addSubjectBtn = document.getElementById('addSubjectBtn');
    const cancelFormBtn = document.getElementById('cancelFormBtn');
    const subjectFormContainer = document.getElementById('subjectFormContainer');
    const subjectForm = document.getElementById('subjectForm');
    const subjectIdInput = document.getElementById('subjectId');

    addSubjectBtn.addEventListener('click', function() {
        subjectForm.reset();
        subjectIdInput.value = '';
        subjectFormContainer.style.display = 'block';
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
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Ошибка при удалении: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Произошла ошибка при удалении');
                });
            }
        });
    });
    
    subjectForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const url = subjectIdInput.value ? `/api/update-subject/${subjectIdInput.value}/` : '/api/add-subject/';
        
        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при сохранении');
        });
    });
});