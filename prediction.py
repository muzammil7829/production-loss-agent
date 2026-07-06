from sklearn.linear_model import LinearRegression
import numpy as np

def predict_loss(loss_values):

    x = np.array(
        range(len(loss_values))
    ).reshape(-1,1)

    y = np.array(loss_values)

    model = LinearRegression()

    model.fit(x,y)

    next_day = np.array(
        [[len(loss_values)]]
    )

    prediction = model.predict(
        next_day
    )

    return round(
        prediction[0],
        2
    )