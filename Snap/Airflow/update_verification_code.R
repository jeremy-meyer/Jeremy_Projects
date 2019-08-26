# Needs DBI / SnapCon package
gen_rand_pin <- function(ndig=5){
  pin <- floor(runif(1, min=10^(ndig-1), max=10^ndig))
  # 3+ distinct digits
  if(length(unique(unlist(strsplit(as.character(pin), '')))) < 3) 
    return(gen_rand_pin(ndig)) 
  pin
}

pin <- gen_rand_pin()
query  <- paste0("UPDATE snapanalytics.sales_msr_verification_code SET code = ", pin,";")
con <- SnapCon::MakeDbConnection('aws')
DBI::dbExecute(con, query)
print(paste('Updated verification code to', pin))
