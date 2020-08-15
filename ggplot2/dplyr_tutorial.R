library(dplyr)

library(downloader)
url <- "https://raw.githubusercontent.com/genomicsclass/dagdata/master/inst/extdata/msleep_ggplot2.csv"
filename <- "msleep_ggplot2.csv"
if (!file.exists(filename)) download(url,filename)
msleep <- read.csv("msleep_ggplot2.csv")
head(msleep)


# dplyr functions ---------------------------------------------------------

# %>%       pipes data into functions
# select()	select columns
# filter()	filter rows
# arrange()	re-order or arrange rows
# mutate()	create new columns
# summarise()	summarise values
# group_by()	allows for group operations in the "split-apply-combine" concept


# Pipe operator %>% (ctr+shift+m) -----------------------------------------
# This puts whatever is on the left inside the first argument of what's on the right
# Instead of nesting several functions, we can just use the pipe operator instead. Makes code much more readable.
c(4,1,5,2,6,NA) %>% mean(na.rm=TRUE)


# Select (Columns) ----------------------------------------------------------------

# Pipe (%>%) allows you to transfer the output of one function directly into the input of another
# No more nesting functions! This promotes readability
# output %>% input

# Select columns
msleep %>% select(name, sleep_total) %>% head(10)
head(select(msleep, name, sleep_total), 10)

# Select ranges
msleep %>% select(4:7)
msleep %>% select(order:sleep_rem)

# Omit columns
msleep %>% select(-genus)

# Rename selected Columns
msleep %>% select(name, 'sleep total' = sleep_total)

## Helper Functions --------------------------------------------------------
# ends_with() = Select columns that end with a character string
# contains() = Select columns that contain a character string
# matches() = Select columns that match a regular expression
# one_of() = Select columns names that are from a group of names

head(select(msleep, starts_with("sl")))


# Filter (rows) ------------------------------------------------------------------

# Only include rows with specified column values
filter(msleep, sleep_total >= 16)
filter(msleep, sleep_total >= 16, vore == 'carni')

# Multiple conditions (OR)
filter(msleep, order %in% c("Perissodactyla", "Primates"))



# Arrange (Sort) -----------------------------------------------------------------

# Orders rows by column order, then vore
msleep %>% arrange(order, vore) %>% head(20)

# Descending order (desc())
msleep %>% arrange(desc(order), vore) %>% head(20)

# Select animals that have total greater than 16, 
# sort by order, then sleep total. 
msleep %>% 
  select(name, order, sleep_total) %>%
  arrange(order, sleep_total) %>% 
  filter(sleep_total > 16)


# Mutate (New Columns) ----------------------------------------------------

# Create new proportion column, % of REM sleep (REM/total)
msleep %>% 
  mutate(rem_proportion = sleep_rem / sleep_total) %>%
  head

# Multiple new columns
msleep %>% 
  mutate(rem_proportion = sleep_rem / sleep_total, 
         bodywt_grams = bodywt * 1000) %>%
  head

msleep %>% transmute(rem_prop = sleep_rem / sleep_total) %>% # Only gives the new column
  head

# Summarise (stats) -------------------------------------------------------
# sd(), min(), max(), quantile(), median(), mean(), sum(), n(), n_distinct(), 

# Mean sleep total
msleep %>% 
  summarise(avg_sleep = mean(sleep_total))

# Sleep total summary statistics
msleep %>% 
  summarise(avg_sleep = mean(sleep_total), 
            min_sleep = min(sleep_total),
            max_sleep = max(sleep_total),
            total = n())

# 2nd moment estimation (custom functions)
EX2 <- function(x) mean(x)^2
msleep %>% 
  summarise(avg2_sleep = EX2(sleep_total))

# Logical operators
msleep %>% 
  summarise('AnyAbove20?' = any(sleep_total > 20),
            'AnyAbove15?' = any(sleep_total > 15),
            'AllAvove0?'  = all(sleep_total > 0))


# Group by() --------------------------------------------------------------

# Summary Statistics for each unique value of order
msleep %>% 
  group_by(order) %>%
  summarise(avg_sleep = mean(sleep_total), 
            min_sleep = min(sleep_total), 
            max_sleep = max(sleep_total),
            total = n())
stat.f <- function(x) c('avg'=mean(x), 'min'=min(x), 'max'=max(x), 'n'=length(x))
aggregate(sleep_total ~ order, data=msleep, FUN=stat.f)
# Which is easier?

msleep %>% group_by(genus)


# Cool graphic
library(nycflights13)
library(ggplot2)

by_tailnum <- group_by(flights, tailnum)
delay <- summarise(by_tailnum,
                   count = n(),
                   dist = mean(distance, na.rm = TRUE),
                   delay = mean(arr_delay, na.rm = TRUE))
delay <- filter(delay, count > 20, dist < 2000)

# -OR-
flights %>% group_by(tailnum) %>% 
  summarise(count = n(), dist = mean(distance, na.rm = TRUE), 
            delay = mean(arr_delay, na.rm = TRUE)) %>% 
  filter(count > 20, dist < 2000)

# Interestingly, the average delay is only slightly related to the
# average distance flown by a plane.
ggplot(delay, aes(dist, delay)) +
  geom_point(aes(size = count), alpha = 1/2) +
  geom_smooth() +
  scale_size_area()
