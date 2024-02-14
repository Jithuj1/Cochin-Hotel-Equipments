from django.conf import settings


def calculate_gst(price, gst_perc, billing_state, billing_country):
    """this function is used to calculate the gst based on
    some parameters and conditons, Basically it return all three gst is zero when
    the billing state is not IN, And if the billing state is not GJ then it return
    values for sgst and cgst in this case igst is zero. If the billing state is not GJ,
    then it will return value for igst other variables are set to zero
    And order of this three variables vary important"""

    tax_igst = tax_sgst = tax_cgst = 0

    bussiness_details = settings.STORE_ADDRESS

    if billing_country != bussiness_details["country"]:
        return tax_igst, tax_sgst, tax_cgst

    elif billing_state == bussiness_details["state"]:
        tax_sgst = tax_cgst = (price * (gst_perc / 100)) / 2
        return tax_igst, tax_sgst, tax_cgst

    else:
        tax_igst = price * gst_perc / 100
        return tax_igst, tax_sgst, tax_cgst