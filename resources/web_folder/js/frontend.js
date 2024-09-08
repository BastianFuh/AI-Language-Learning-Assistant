




eel.expose(update)
function update(data) {

    console.log(data)

    text = data["data"]
    //text.strip()
    text = text.replace("\n", "<br />")

    console.log(text)

    html = `
<div id="card" class="card p-3 align-self-start  mt-4 w-50 bg-secondary text-light fs-5">
    <div class="fs-4 fw-bold card-title">
        Test
    </div>
    <div class="card-body">
        <p>
            ${text}
        </p>
    </div>
</div>

`

    window.document.getElementById("text-container").innerHTML += html
}


function send_text_to_backend() {
    text = document.getElementById("text-input").value
    console.log("Send text")
    eel.process_frontend_text(text)
}


document.getElementById("btn-submit-text-input").addEventListener("click", send_text_to_backend)