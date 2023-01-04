import express from "express";
import axios from "axios";

const dataRouter = express.Router();

dataRouter.get("/",(req,res)=>{
    res.send("hello");
})


export default dataRouter