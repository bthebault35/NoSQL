##############################################################################
####################### Projet - Requêtes MongoDB en R #######################
##############################################################################

library(mongolite)
library(tidyverse)
library(ggplot2)

######################## Connexion à la base de données ######################

mdb = mongo(collection="hal_irisa_2021", db="publications",
           url="mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/",
           verbose=TRUE)

############################# Requêtes de lecture ############################

######### 1. Récupérer la listes des 20 auteurs les plus prolifiques #########

#Requête MongoDB
#db.hal_irisa_2021.aggregate([{ $unwind : "$authors" }, 
#                             { $group : { _id : "$authors", number : { $sum : 1 } }}, 
#                             {$sort : {number : -1}}] )

q1='[
    {"$unwind" : "$authors"}, 
    {"$group" : {"_id" : {"Name":"$authors.name","First_name":"$authors.firstname"}, "number" : { "$sum" : 1 } }}, 
    {"$sort" : {"number" : -1}},
    {"$limit": 20}
]'

df1 <- mdb$aggregate(pipeline=q1)
df1$name <- df1$'_id'$Name
df1$firstname <- df1$'_id'$First_name
df1 <- df1 %>% select(name, firstname, number)

df1

################## 2. Récupérer pour chacun de ces auteurs la #################
################# liste des publications dont il a participé. #################

df2 = data.frame(matrix(vector(), 0, 3, dimnames=list(c(), c("nom","prenom","titres"))),stringsAsFactors=F)

for (i in 1:nrow(df1)){
  n <- as.character(df1[i,1])
  p <- as.character(df1[i,2])
  query=paste('{"authors":{"$elemMatch":{"name":"',n,'", "firstname":"',p,'"}}}',sep="")
  titres <- mdb$find(query = query ,fields = '{"title":true}') %>% select(title)
  t <- list(titres)
  df2 <- rbind(df2, data_frame(nom=n,prenom=p, titres=t)) 
}

df2

######## 3. Calculer le nombre d’articles communs par paire d’auteurs. ########

