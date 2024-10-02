// Menampilkan nilai slider dalam format angka pada elemen <span>
document.getElementById('age').addEventListener('input', function(event) {
    document.getElementById('displayAge').innerText = event.target.value;
});
