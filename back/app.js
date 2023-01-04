import express from "express";
import axios from "axios";
import dotenv from "dotenv";
import env from "./index.js";
import dataRouter from "./mydata.js";
import bodyParser from "body-parser";


const app = express();

app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

app.use("/mydata", dataRouter);

app.listen(env.PORT, ()=>{
    console.log(`
        server started
    `);
}).on("error",(err)=>{
    console.error(err);
    process.exit(0);
});