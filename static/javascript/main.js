// let x;

// function myFunction(p1,p2) {
//      // The function returns the product of p1 and p2
//     return p1*p2
//   }

// x=myFunction(4,100)
// console.log(x)



// const paragraphs = document.getElementById("like")
// document.getElementById("like").onclick=myFunction(paragraphs)

// function myFunction() {
//     const like_button = document.getElementById("like")
//     if (like_button.style.color === "white") {
//         // block of code to be executed if the condition is true
//         like_button.style.color === "blue";
//       } else if (like_button.style.color = "blue"){
//         // block of code to be executed if the condition is false
//         like_button.style.color = "white";
//       } else {
//           like_button.style.color = "red"
//       }
// }


function myFunction(){
    // let button1 = document.getElementById("4");

    // switch (button1.style.color) {
    //   case "":
    //     button1.style.color = "blue"
    //     break;
    //   case "blue":
    //     button1.style.color= "red"
    //     break
    //   case "red":
    //     button1.style.color = ""
    //     break
    // }

    // switch (button1.innerHTML) {
    //   case "Click Me!":
    //     button1.innerHTML = "goodbye"
    //     break;
    //   case "goodbye":
    //     button1.innerHTML = "Click Me!"
    //     break
    // }

    // // create a button element
    // const button2 = document.createElement("button");
    // document.body.appendChild(button2);

    const likeButton = document.getElementById("like")
    likeButton.src = "/static/preview_img/red heart.png"
}

// for (let i = 0; i < 20; i++) {
//     var tag = document.createElement("p").innerHTML = "Num is " + i;
//     console.log(tag)
//     // document.body.appendChild(tag);
//     // var tag2 = document.getElementsByTagName("p");
//     // tag2.innerHTML = "hello " + i
// }

var mysql = require('mysql');

var con = mysql.createConnection({
  host: "localhost",
  user: "myusername",
  password: "mypassword",
  database: "mydb"
});

con.connect(function(err) {
  if (err) throw err;
  //Select all customers and return the result object:
  con.query("SELECT * FROM customers", function (err, result, fields) {
    if (err) throw err;
    console.log(result);
  });
});