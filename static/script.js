function loadNotes() {

    fetch("/notes")
    .then(response => response.json())
    .then(data => {

        let notesDiv = document.getElementById("notes");
        notesDiv.innerHTML = "";

        data.forEach(function(note){

    notesDiv.innerHTML += `
    <div class="note-item">
        <div>
            <span>📝 ${note[1]}</span><br>
            <small>📅 ${note[2]}</small>
        </div>

        <div>
            <button onclick="editNote(${note[0]}, '${note[1]}')">
                Edit
            </button>

            <button onclick="deleteNote(${note[0]})">
                Delete
            </button>
        </div>
    </div>
`;

});

    });

}

document.getElementById("saveBtn").addEventListener("click", function () {

    let note = document.getElementById("note").value;

    fetch("/save", {

        method: "POST",

        headers: {
            "Content-Type":"application/json"
        },

        body: JSON.stringify({
            note: note
        })

    })

    .then(response => response.json())

    .then(data => {

        alert(data.message);

        document.getElementById("note").value = "";

        loadNotes();

    });

});

loadNotes();
function deleteNote(id) {
    fetch(`/delete/${id}`, {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        location.reload();
    });
}
function editNote(id, oldNote) {

    let newNote = prompt("Edit your note:", oldNote);

    if (newNote === null || newNote.trim() === "") {
        return;
    }

    fetch(`/edit/${id}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            note: newNote
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        location.reload();
    });
}
function searchNotes() {

    let input = document.getElementById("search").value.toLowerCase();

    let notes = document.getElementsByClassName("note-item");

    for (let i = 0; i < notes.length; i++) {

        let text = notes[i].innerText.toLowerCase();

        if (text.includes(input)) {
            notes[i].style.display = "flex";
        } else {
            notes[i].style.display = "none";
        }
    }
}