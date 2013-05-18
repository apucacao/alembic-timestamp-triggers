# Generate SQL for automatically updating timestamp columns.

def __name(table, column):
  return "{table}_{column}".format(table=table, column=column)

def create_function_sql(name, definition, returns='trigger'):
  """Generate SQL for creating a function."""
  return """
  CREATE OR REPLACE FUNCTION {name} ()
    RETURNS {returns}
    LANGUAGE 'plpgsql'
    AS $${definition}$$;
  """.format(name=name, definition=definition, returns=returns)

def drop_function_sql(name):
  """Generate SQL for dropping a function."""
  return "DROP FUNCTION IF EXISTS {name}();".format(name=name)

def create_trigger_sql(table, trigger_name, function_name, events=['INSERT', 'UPDATE']):
  """Generate SQL for creating a trigger."""
  return """
  CREATE TRIGGER {name} BEFORE {events} on {table}
  FOR EACH ROW EXECUTE PROCEDURE {function}();
  """.format(
    name=trigger_name,
    events=' OR '.join(events),
    table=table,
    function=function_name
  )

def drop_trigger_sql(table, name):
  """Generate SQL for dropping a trigger."""
  return "DROP TRIGGER IF EXISTS {name} on {table};".format(name=name, table=table)

def create_timestamp_trigger(table, column, definition):
  """Generate SQL for udpating a timestamp column."""
  name = __name(table, column)
  create_function = create_function_sql(name, definition)
  create_trigger = create_trigger_sql(table, name, name)
  return "\n".join([create_function, create_trigger])

def drop_timestamp_trigger(table, column):
  """Generate SQL for dropping a timestamp trigger on a column."""
  name = __name(table, column)
  drop_function = drop_function_sql(name)
  drop_trigger = drop_trigger_sql(table, name)
  return "\n".join([drop_trigger, drop_function])

def create_timestamp_trigger_for_creation(table, column='created'):
  """Generate SQL for updating a timestamp column on creation."""
  return create_timestamp_trigger(table, column, """
  BEGIN
    IF (TG_OP = 'UPDATE') THEN
      NEW.{column} := OLD.{column};
    ELSIF (TG_OP = 'INSERT') THEN
      NEW.{column} := CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
  END;
  """.format(column=column))

def drop_timestamp_trigger_for_creation(table, column='created'):
  """Generate SQL to stop updating a timestamp column on creation."""
  return drop_timestamp_trigger(table, column)

def create_timestamp_trigger_for_modification(table, column='modified'):
  """Generate SQL for updating a timestamp column on modification."""
  return create_timestamp_trigger(table, column, """
  BEGIN
    NEW.{column} := CURRENT_TIMESTAMP;
    RETURN NEW;
  END;
  """.format(column=column))

def drop_timestamp_trigger_for_modification(table, column='modified'):
  """Generate SQL to stop updating a timestamp column on modification."""
  return drop_timestamp_trigger(table, column)