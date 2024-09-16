




eel.expose(update)
function update(data) {

    console.log(data)

    text = data["data"]
    //text.strip()
    text = text.replace("\n", "<br />")

    console.log(text)

    // Default lable and alignment
    label = `User (${data["source"]})`
    text_alignment = "align-self-end me-3"

    // 
    if (data["source"] === "llm") {
        label = `System (${data["source"]})`
        text_alignment = "align-self-start ms-3"
    }


    html = `
<div id="card" class="card p-3 ${text_alignment} mt-4 w-50 bg-secondary text-light fs-5">
    <div class="fs-4 fw-bold card-title">
        ${label}
    </div>
    <div class="card-body">
        <p>
            ${text}
        </p>
    </div>
</div>

`

    text_container = window.document.getElementById("text-container")

    text_container.innerHTML += html
    text_container.scrollTo(0, text_container.scrollHeight)


}


function send_text_to_backend() {
    text_input = document.getElementById("text-input")
    text = text_input.value
    console.log("Send text")
    eel.process_frontend_text(text)
    text_input.value = ""
}


document.getElementById("btn-submit-text-input").addEventListener("click", send_text_to_backend)

eel.get_data()