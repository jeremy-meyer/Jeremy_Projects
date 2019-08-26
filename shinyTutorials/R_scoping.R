# Scoping assignment
# Enclosing environments are searched until x is encountered
new_counter <- function() {
  i <- 0
  function() {
    # do something useful, then ...
    i <<- i + 1
    i
  }
}

counter_one <- new_counter()
counter_two <- new_counter()

x <- 1
y <- -5
f <-function(x1,y1,z1){
  x <<- x1
  y <<- y1
  z <<- z1
}
f(4,5,1)
c(x,y,z)

# Useful because the server() function is user-specific. But if changes need to be made globally, use the scope

varA <- 1
varB <- 1
listA <- list(X = 1, Y = 2) # Big-data set accessed by all users
listB <- list(X = 1, Y = 2)

server <- function(input, output, session) {
  # Create a local variable varA, which will be a copy of the shared variable
  # varA plus 1. This local copy of varA is not be visible in other sessions.
  varA <- varA + 1
  
  # Modify the shared variable varB. It will be visible in other sessions.
  varB <<- varB + 1
  
  # Makes a local copy of listA
  listA$X <- 5
  
  # Modify the shared copy of listB
  listB$X <<- 5
  
  # ...
}