$("document").ready(function(){
    $("#send").click(function(){
        var name = $("#name").val();
        var password = $("#password").val();

        $.ajax({
            url: "http://localhost:5000/register",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({"message": "registered successfully"})
        }).done(function(data)
        {
            console.log(data);
        });
    });
});