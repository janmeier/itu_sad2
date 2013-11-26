Forklaring af filerne i denne mappe

AlgProjectParsing.py
Koden kan parse nedenstående fil og finde connected components i grafen

imdbMovieActorLastTenYears.csv
En fil af samme format som Spielberg filen vi fik udleveret. Indeholder kombinationen af movies, actors og roles.
Dermed er der en linje for alle roller spillet i alle film. Denne fil kan bruges til at bygge grafen med.
Filen indeholder dog kun data for alle film efter 2002 da parsingen ellers bruger mere end 2gb memory, hvilket vist ikke er muligt når man kører python på windows.. 
Filen er lavet med denne kommando:
select m.name, m.id, m.rank, m.year, a.first_name, a.last_name, a.id, a.film_count from actors as a, movies as m, roles as r where m.id = r.movie_id and a.id = r.actor_id and m.year > 2002 order by m.id into outfile "C:/python33/imdbMovieActorLastTenYears.csv" fields terminated by ';' lines terminated by '\n';
databasen er lavet med dette script: http://www.webstepbook.com/supplements-2ed/databases/imdb.zip. (fundet på kursusbloggen)