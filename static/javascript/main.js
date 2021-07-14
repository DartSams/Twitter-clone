// function myFunction(p1) {
//     console.log(p1);   // The function returns the product of p1 and p2
// }


// const paragraphs = document.getElementById("like")
// document.getElementById("like").onclick=myFunction(paragraphs)

function myFunction() {
    const like_button = document.getElementById("like")
    if (like_button.style.color === "white") {
        // block of code to be executed if the condition is true
        like_button.style.color === "blue";
      } else if (like_button.style.color = "blue"){
        // block of code to be executed if the condition is false
        like_button.style.color = "white";
      } else {
          like_button.style.color = "red"
      }
    // console.log(like_button.innerHTML)
}
