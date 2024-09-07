




eel.expose(update)
function update(data) {

    console.log(data)

    html = `
<div id="card" class="card p-3 align-self-start  mt-4 w-50 bg-secondary text-light fs-5">
    <div class="fs-4 fw-bold card-title">
        Test
    </div>
    <div class="card-body">
        ${data["data"]}
    </div>
</div>

`

    window.document.getElementById("text-container").innerHTML += html
}