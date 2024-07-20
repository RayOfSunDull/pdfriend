# Contributing

If you somehow found this and want to contribute features or fixes, please open a github issue first.


## Feature requirements
This project is not conservative in terms of features, and I'll generally add anything that seemes even a little useful; the main purpose of this editor is being able to make quick-and-dirty changes to PDFs. The exception to this is dependencies, which should be kept at a minimum. I will only add a dependency if I feel like it provides sufficient benefit.

## Style
Try to follow the style I use in the source. Using a formatter like [black](https://github.com/psf/black) should also be adequate.

## Testing
You should run the tests before sumbitting a pull request. On Linux, this can be done as such:

```sh
git clone https://github.com/RayOfSunDull/pdfriend
cd pdfriend/tests
source init.sh
```

This will create a venv in `pdfriend/tests/.venv` with pdfriend and [pytest](https://docs.pytest.org/en/8.2.x/) installed. After doing this setup step, you can activate it in later sessions by running `source launch.sh`. It should be very straightforward to port these scripts to Windows.

After making whatever changes you want, you can do the tests by running `pytest` while in the test venv. You *must* be in the `pdfriend/tests` directory for it to work.

Thanks for your interest!
