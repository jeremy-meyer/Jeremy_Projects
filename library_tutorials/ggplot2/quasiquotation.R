# Quasiquotation

library(rlang)
library(purrr)

# This is great, but typing all the quotes is annoying
paste("Good", "afternoon", "Alice")


cement <- function(...) {
  args <- ensyms(...)
  paste(purrr::map(args, as_string), collapse = " ")
}

cement(Good, afternoon, Alice) # No quotation needed, automatically puts them there



## However, if we want to do this
name <- "Hadley"
time <- "morning"

paste("Good", time, name)
cement(Good, time, name) # Problem

cement(Good, !!time, !!name) # Tells R to unquote these and use the stored value


## Vocab
# Evaluated arguement (traidtional R rules). Paste
# Quoted arguement (captured instide function) cement

library(MASS) # Quoted arguement
MASS # Doesn't work! 


# More examples
library(ggplot2)
library(dplyr)

by_cyl <- mtcars %>%
  group_by(cyl) %>%
  summarise(mean = mean(mpg))

ggplot(by_cyl, aes(cyl, mean)) + geom_point() # AES contains quoted strings


## Expressions
x <- 3
y <- 14
expr(x+y) #quote() base R

f1 <- function(x) expr(x)
f1(a + b + c) # Didn't do what I wanted

f2 <- function(x) enexpr(x) # substitute() base R
f2(a + b + c) # There we go

## Double bang ---------------------------------------
## Unquoting. Inverse of quoting
x <- 5
expr(x)
expr(!!x)

eval(expr(x)) # Also an interse
expr(f(x,y))
expr(f(!!x,y)) # Allos you to use a stored value inside a quoted value

# Special forms
x <- expr(x)
expr(`$`(df, !!x))

## Triple Bang. One to many unpacking of expressions
xs <- exprs(1, a, -b)
expr(f(!!!xs, y))

df <- data.frame(x = 1:5)
y <- 100
with(df, x + !!y) # Silent errors. 

# Symbols
x <- 5
sym('x')
class(sym('x')) # This is a name
class(expr(x))
eval(sym('x'))

# Example -----------------------------------------------------------------
library(ggplot2)

# I want to do this
ggplot(iris) + geom_point(aes(x=Sepal.Length, y=Sepal.Width))

f.naive <- function(col.x, col.y){
  ggplot(data=iris) + geom_point(aes(x=col.x, y=col.y))
}

# This treats these names as strings
f.naive('Sepal.Length', 'Sepal.Width') # It's treating these column names as strings
ggplot(iris) + geom_point(aes(x='Sepal.Length', y='Sepal.Width'))



n1 <- 'Sepal.Length'
sym(n1) # Convert to name, and then use !! to evaluate it. Can also use eval()
# Remember !! gets the stored value in the environment inside a quoted value. Without it, we just have the name. 
ggplot(iris) + geom_point(aes(x=eval(as.name('Sepal.Length')), y=!!sym('Sepal.Width')))

f.works <- function(dat, col.x, col.y){
  ggplot(data=get(dat)) + geom_point(aes(x=!!sym(col.x), y=!!sym(col.y)))
}
f.works('iris', 'Sepal.Length', 'Sepal.Width')
