let express = require('express');
const { dbConnection } = require('./dbConnection');

let app=express();

app.use(express.json())

app.get('/student-read',async (req,res)=>{

    let myDB= await dbConnection()   // will return db from that func and store in this variable 

    let studentCollection = myDB.collection('students')

    let data = await studentCollection.find().toArray();

    let responseObj = {
        status:1,                       // for frotend devs to know
        msg:"data viewing done",
        data
    }


    res.send(responseObj)
 })

app.post('/student-insert',async (req,res)=>{

    let myDB= await dbConnection()   // will return db from that func and store in this variable 

    let studentCollection = myDB.collection('students')

    // let obj={
    //     sname: req.body.sname,
    //     email: req.body.email
    // }

    // alternative - destructucring

    const {sname,email}=req.body;

    let obj =(sname,email);
    //insert
    let insert = await studentCollection.insertOne(obj);
    // console.log(obj);
    let responseObj = {
        status:1,                       // for frotend devs to know
        msg:"data insert done",
        insert
    }

    res.send(responseObj)
    console.log(responseObj)
})

app.listen('8000')