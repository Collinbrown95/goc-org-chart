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
  lang = req.query["lang"];
  console.log(team_name);
  console.log(lang);
  url = config.gedsServer + "/search-team" + "?team_name=" + team_name + "&lang=" + lang;
  request(url, function(error, response, body){
    console.log('error: ', error);
    console.log('statusCode: ', response && response.statusCode);
    console.log('body: ', body);
    res.send({
      body: body
    })
  });
});

router.get('/search-person', function(req,res){
  person_name = req.query["person_name"];
  lang = req.query["lang"];
  console.log(person_name);
  console.log(lang);
  url = config.gedsServer + "/search-person" + "?person_name=" + person_name + "&lang=" + lang;
  request(url, function(error, response, body){
    console.log('error: ', error);
    console.log('statusCode: ', response && response.statusCode);
    console.log('body: ', body);
    res.send({
      body: body
    })
  });
});

router.get('/search-org-chart', function(req,res){
  person_name = req.query["team_name"];
  lang = req.query["lang"];
  console.log(person_name);
  console.log(lang);
  url = config.gedsServer + "/search-org-chart" + "?team_name=" + person_name + "&lang=" + lang;
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