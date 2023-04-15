from django import template
import datetime

from tree_menu.models import Item

register = template.Library()


@register.inclusion_tag('tree_menu/nested_menu.html', takes_context=True)
def draw_tree_menu(context, menu: str) -> dict:
    try:
        # !!!!Do request to the base and get items from given menu name!!!!!
        items = Item.objects.filter(menu__title=menu)
        # Obtain list with dicts of param values for each item
        items_values = items.values()
        # Obtain list with param dicts for items without parent
        primary_item = [item for item in items_values.filter(parent=None)]
        # Return currently selected id's of items from context data (request from current menu)
        selected_item_id = int(context['request'].GET[menu])
        # According to id has found
        selected_item = items.get(id=selected_item_id)
        # Get list of id for selected item
        selected_item_id_list = get_selected_item_id_list(parent=selected_item,
                                                          primary_item=primary_item,
                                                          selected_item_id=selected_item_id)

        # For each item without parent
        for item in primary_item:
            if item['id'] in selected_item_id_list:
                item['child_items'] = get_child_items(items_values, item['id'], selected_item_id_list)
        result_dict = {'items': primary_item}

    except:
        result_dict = {
            'items': [
                item for item in Item.objects.filter(menu__title=menu, parent=None).values()
                ]
            }

    result_dict['menu'] = menu
    # prepare results for other menu if such exist
    result_dict['other_querystring'] = get_querystring(context, menu)

    return result_dict


def get_querystring(context, menu):
    querystring_args = []
    # get the dict with request header
    for key in context['request'].GET:
        # if param header is not equal name of menu then form query string unit for this key
        if key != menu:
            querystring_args.append(f"{key}={context['request'].GET[key]}")
    querystring = ('&').join(querystring_args)
    return querystring


def get_child_items(items_values, current_item_id, selected_item_id_list):
    item_list = [item for item in items_values.filter(parent_id=current_item_id)]
    for item in item_list:
        if item['id'] in selected_item_id_list:
            item['child_items'] = get_child_items(items_values, item['id'], selected_item_id_list)
    return item_list


def get_selected_item_id_list(parent, primary_item, selected_item_id):
    selected_item_id_list = []
    # While we don't get item without parent
    while parent:
        selected_item_id_list.append(parent.id)
        parent = parent.parent
    if not selected_item_id_list:
        for item in primary_item:
            if item['id'] == selected_item_id:
                selected_item_id_list.append(selected_item_id)
    return selected_item_id_list
