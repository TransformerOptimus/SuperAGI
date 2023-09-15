const express = require('express');
const {dom_extractor} = require('./dom_extractor.js');
const app = express();
const fs = require('fs');

app.use(express.json({limit: '50mb'}));
app.use(express.urlencoded({limit: '50mb'}));


app.get('/health', (req, res) => {
    res.send('OK');
})


app.post("/transformed_html", (req, res) => {
//    console.log(req)
    const body = req.body;
//    console.log(body)
    const {dom_content, goal} = body;
    if(goal=="TYPE 'https://gokwik.co/'->domain-input"){
        fs.writeFileSync("./goal",goal)
        fs.writeFileSync('./dom',dom_content)
    }
    const transformed_html = dom_extractor(dom_content, goal);
    res.send({transformed_dom: transformed_html});
});




app.listen(7000, () => {
    console.log("Server running on port 7000");
});