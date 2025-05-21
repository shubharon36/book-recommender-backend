// server
// let http=require('http')

// let server = http.createServer((req,res)=>{
//         res.end('Hello')
// })

// server.listen('8000')

let express = require('express')
const { checkToken } = require('./checkTokenMiddleware')

require('dotenv').config() // init dotenv stuff

let app = express()
app.use(express.json())

console.log(process.env.mytoken)
// middleware 

// let mytoken = 123;

// let checkToken = (req,res,next)=>{
//    // console.log('Welcome now')

//     if(req.query.token="" || req.query.token==undefined){
//         return res.send({
//             status:0,
//             msg:'fill it'          
//              // this will be displayed and not /news when we hit that route
//         })
//     }

//     if(req.query.token!=mytoken){
//         return res.send({
//             status:0,
//             msg:'fill it correct'
//         })

//     }

//     next(); 
//     // allowing to bypass middleware to the route 
// }

// app.use(checkToken) // before going any route it will pass middleware to check



app.get('/',(req,res)=>{
    res.send('He')
})

app.get('/news',checkToken,(req,res)=>{   // route level middleare ie only on this route will show
    res.send({hi:'2', hi2:'bj'})
})

app.get('/prods/:id',(req,res)=>{

    let currentProd = req.params.id;

    res.send('prods'+currentProd)
})

app.post('/login',(req,res)=>{
    console.log(req.body)

    res.status(200).json({hehe:'12',hey:'ji'})  // alt way

  //  res.send({hehe:'12',hey:'ji'})
})

app.listen('8000')