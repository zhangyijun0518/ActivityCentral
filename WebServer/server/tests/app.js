var createError = require('http-errors');
var express = require('express');
var path = require('path');

var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');

const {Client} = require('@elastic/elasticsearch');
const client = new Client({

			node: 'https://6e07bdab217747e4beb2f634f7191aad.us-central1.gcp.cloud.es.io:9243',
			auth: {
				username: 'elastic',
				password: 'cp0L47hjYNuPwv1axfTtRJX4'
			}
	});

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, 'public')));


app.use('/', async (req, res) => {
	const {body} = await client.search({
			index: 'ac',
			type: 'activity',
			body: {
				query: {
					bool: {
						filter: [
							{match: {name: 'Symposium Online' }},
								//'Wi3DP North America Virtual Happy Hour'}},
							{match: {organizer: 'Citizens of One'}},
								// 'Nora Toure'}},
							{term: 	{activity_date: '0'}}
						]
					}
				}
			}
		}).catch(err => {
			console.log(err.body);
		});
		console.log(body);
	console.log(body.hits);
	res.json({
		count: body.hits.total.value,
		results: body.hits.hits
	});
});

app.use('/', indexRouter);
app.use('/users', usersRouter);



// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});


app.listen(4000, () => {

});
module.exports = app;
