def divide(x, y):
    try:
        result = x / y
    except ZeroDivisionError:
        print "division by zero!"
    else:
        print "result is", result


while True:
    x = int(raw_input("Please enter a number: "))
    y = int(raw_input("Please enter a number: "))
    divide(x,y)