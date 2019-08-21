var express = require('express');
var router = express.Router();
var request = require("request");
var config = require('../modules/config.js');

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index');
});

router.get('/search-team', function(req,res){
  team_name = req.query["team_name"];
  url = config.gedsServer + "?team_name=" + team_name;
  request(url, function(error, response, body){
    console.log('error: ', error);
    console.log('statusCode: ', response && response.statusCode);
    console.log('body: ', body);
    res.send({
      body: body
    })
  });
});

module.exports = router;