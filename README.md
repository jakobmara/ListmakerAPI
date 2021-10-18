# List Maker API

<h2> What is this </h2>
<p>This is a Flask REST API I created (hosted on Heroku) to interact with MySQL database.</p>

<h2>What is the purpose of this</h2>
<p>The goal of the API was to give users the ability to create and edit lists of their favorite TV shows or movies.</p>

<h2>Implementation</h2>
<p>Currently the API uses the TMDB API for information when it comes to TV shows and movies. The API also has support for anime but because there was no useful anime API, it has to scrape the web to get accurate information which results in more latency compared to the other categories.</p>

<h2>Technologies</h2>
<ul>
<li>Python</li>
<li>Flask</li>
<li>BeautifulSoup</li>
<li>MySQL</li>
</ul>