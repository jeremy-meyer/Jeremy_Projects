context("Data generation method is normal")

# Generates false positive .1% of the time
test_that("Method passes KS test!", {
  expect_gt(ks.test(rand_data(), 'pnorm', sd=10)$p.val, 0.001)
})