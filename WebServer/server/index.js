const express=require('express');
const app = express();
const config = require('./config');
const path = require('path');

const activityRouter = require('./routes/activity');
const userRouter = require('./routes/user');

const db = require('./models');



// if (config.debug) {
// 	//db.sequelize.sync({force:true});
// } else {
// 	db.sequelize.sync();
// }

db.sequelize.sync();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// app.get('/', (req, res) => {
// 	res.send("hello world");
// });

app.use('/', activityRouter);
app.use('/', userRouter);
app.use('/', require('./routes/recommand'));

//app.use('/test', require('./test/app'))

app.use((req, res, next) => {
	res.json({err: 'url not found'});
});

app.use((err, req, res, next) => {
	if (config.debug) {
		console.log(err);
	}
	if (err.name === 'UnauthorizedError') {
		return res.json({ err: err.message });
	}
	res.json({err: err});
})

app.listen(config.port, ()=>{
	if (config.debug) {
		console.log('example listening');
	}
});